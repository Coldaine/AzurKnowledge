# Goal

* Trigger **incremental** script compile from the Editor on demand.
* Return immediately (non-blocking call site); let Unity’s own pipeline run.
* Debounce + coalesce requests so you don’t thrash the compiler.
* Optional: a tiny MCP server “pinger” that periodically asks Unity to compile **only if there’s something to do**.
* Never use “clean”/full rebuild by default.

Unity already supports exactly this: `CompilationPipeline.RequestScriptCompilation()` checks for script (or relevant settings) changes and **only recompiles what’s needed**; otherwise it’s a no-op. There’s also a “clean build cache” option—but don’t use it unless you truly want a full rebuild. ([Unity Documentation][1], [Unity User Manual][2])

---

## 1) Editor-side: one tiny, non-blocking “compile-if-needed” command

Drop this into an Editor folder:

```csharp
using System;
using UnityEditor;
using UnityEditor.Compilation;

[InitializeOnLoad]
public static class McpCompileIfNeeded
{
    // Coalesce & rate-limit requests
    static DateTime _lastRequestUtc = DateTime.MinValue;
    static bool _queued;

    static McpCompileIfNeeded()
    {
        // When a compile finishes, run any queued request once.
        CompilationPipeline.compilationFinished += _ =>
        {
            if (_queued)
            {
                _queued = false;
                EditorApplication.delayCall += CompileIfNeeded; // schedule on main thread
            }
        };
    }

    [MenuItem("MCP/Compile (Incremental) %#r")] // Ctrl/Cmd+Shift+R
    public static void CompileIfNeeded()
    {
        // Don't pile requests while a compile is in flight
        if (EditorApplication.isCompiling) { _queued = true; return; }

        // Simple debounce (avoid excessive filesystem scans)
        if ((DateTime.UtcNow - _lastRequestUtc).TotalSeconds < 2) return;
        _lastRequestUtc = DateTime.UtcNow;

        // Ask Unity to recompile only if scripts or relevant settings changed.
        // This returns immediately; Unity handles the actual work.
        CompilationPipeline.RequestScriptCompilation(RequestScriptCompilationOptions.None);
    }
}
```

Why this works:

* `RequestScriptCompilation(None)` is incremental and a no-op if nothing changed. **Do not** pass `CleanBuildCache` unless you want a full clean build. ([Unity Documentation][1], [Unity User Manual][2])
* Subscribing to `CompilationPipeline.compilationFinished` lets you **coalesce** overlapping requests (queue one follow-up). ([Unity Documentation][3])
* Checking `EditorApplication.isCompiling` avoids re-entrancy & thundering herd. ([Unity Documentation][4])

Optional: capture warnings/errors by also listening to `CompilationPipeline.assemblyCompilationFinished` if you want to surface diagnostics back to MCP. ([Unity Documentation][5])

> Note: The API call returns immediately (so your MCP request handler isn’t blocked), but the Editor itself will still pause during actual compile—Unity behavior. The point here is: **no blocking at your call-site and no forced clean compiles.** ([Unity Discussions][6])

---

## 2) Expose as an MCP command (Unity side)

If you’re already registering MCP commands inside your Unity bridge, have the command route to `McpCompileIfNeeded.CompileIfNeeded()`. It safely does nothing if a compile is already running or if nothing changed.

You might also add a **rarely-used** parameter like `forceClean: false` that, when `true`, calls:

```csharp
CompilationPipeline.RequestScriptCompilation(RequestScriptCompilationOptions.CleanBuildCache);
```

…but gate it behind confirmation because that **does** trigger a full rebuild. Default should remain incremental. ([Unity User Manual][2])

---

## 3) MCP server: optional periodic “poke” (configurable)

If you want the MCP server to nudge Unity periodically **in case Auto-Refresh is off or changes were made externally**, add a simple timer that calls the command above. Because the Editor-side command is incremental + debounced, this is safe and cheap.

Example config idea:

```toml
[unity.recompile]
enabled = true
interval_seconds = 15
debounce_seconds = 2   # matches editor side
only_when_playmode = "NotPlaying"  # skip if in Play Mode
```

Example pseudo (Python-ish):

```python
def poll_compile_if_needed(client, interval=15):
    while True:
        # fire-and-forget; Editor-side handler does gating & no-ops if clean
        client.call("unity.compileIfNeeded")
        time.sleep(interval)
```

Why “poke” at all?

* When **Auto Refresh** is disabled, Unity won’t import/compile until a refresh or request is made. A light periodic request is a pragmatic way to pick up queued changes without user action. The request itself is effectively a “check & compile if needed,” not a forced import. ([Unity Documentation][7])

> Avoid calling `AssetDatabase.Refresh()` on a timer—that can kick off wide asset imports and a GC sweep; keep it manual or event-driven. Use refresh only when you intentionally want broader asset import behavior. ([Unity Documentation][8])

---

## 4) Don’ts (to prevent “huge compiles”)

* ❌ Don’t pass `CleanBuildCache` unless the user explicitly asks for a clean rebuild. ([Unity User Manual][2])
* ❌ Don’t spam `AssetDatabase.Refresh()` on an interval; it re-imports changed assets and can prolong cycles. Use your menu item (or MCP command) instead. ([Unity Documentation][8])
* ❌ Don’t trigger compiles while one is already running — check `EditorApplication.isCompiling` (the code above handles this). ([Unity Documentation][4])

---

## 5) Nice-to-haves

* Surface compile diagnostics to MCP by listening to `assemblyCompilationFinished` and aggregating `CompilerMessage[]` for errors/warnings. ([Unity Documentation][9])
* Consider a shortcut (Ctrl/Cmd+Shift+R) so users can manually nudge a compile when Auto Refresh is off, without touching assets. (Equivalent to “Assets → Refresh” behavior for *scripts*, but narrower/cheaper because it talks to the compilation pipeline directly.) ([Unity Documentation][7])

---

### TL;DR

Use `CompilationPipeline.RequestScriptCompilation(RequestScriptCompilationOptions.None)` behind a debounced, queued Editor command and optional MCP timer. It’s incremental by design, returns immediately, and is a no-op when nothing changed—so you get your “non-blocking, easy, and safe” trigger without accidentally forcing big rebuilds. ([Unity Documentation][1])

If you want, I can package this into a ready-to-merge PR (Editor script + minimal MCP endpoint + optional diagnostics).

[1]: https://docs.unity3d.com/6000.1/Documentation/ScriptReference/Compilation.CompilationPipeline.RequestScriptCompilation.html?utm_source=chatgpt.com "Unity - Scripting API: Compilation.CompilationPipeline ..."
[2]: https://docs.unity.cn/cn/current/ScriptReference/Compilation.CompilationPipeline.RequestScriptCompilation.html?utm_source=chatgpt.com "Compilation.CompilationPipeline-RequestScriptCompilation - Unity 脚本 API"
[3]: https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Compilation.CompilationPipeline-compilationFinished.html?utm_source=chatgpt.com "Unity - Scripting API: Compilation.CompilationPipeline.compilationFinished"
[4]: https://docs.unity3d.com/6000.2/Documentation/ScriptReference/EditorApplication-isCompiling.html?utm_source=chatgpt.com "Unity - Scripting API: EditorApplication.isCompiling"
[5]: https://docs.unity3d.com/ScriptReference/Compilation.CompilationPipeline-assemblyCompilationFinished.html?utm_source=chatgpt.com "Unity - Scripting API: Compilation.CompilationPipeline ..."
[6]: https://discussions.unity.com/t/incremental-script-compilation/820499?utm_source=chatgpt.com "Incremental script compilation - Unity Engine - Unity Discussions"
[7]: https://docs.unity3d.com/2020.2/Documentation/Manual/AssetDatabaseRefreshing.html?utm_source=chatgpt.com "Unity - Manual: Refreshing the Asset Database"
[8]: https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetDatabase.Refresh.html?utm_source=chatgpt.com "Unity - Scripting API: AssetDatabase.Refresh"
[9]: https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Compilation.CompilationPipeline-assemblyCompilationFinished.html?utm_source=chatgpt.com "Unity - Scripting API: Compilation.CompilationPipeline ..."
