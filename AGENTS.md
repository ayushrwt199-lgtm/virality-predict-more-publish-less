<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## App conventions
- Keep the VIRALITY experience presentation-only; browser session state drives uploads, sample history, and illustrative previews without backend calls.
- Gate the audience workspace behind the upload animation state; cancel its timer on reset or replacement to avoid stale reveals.
- Keep reusable brand and audience-map visuals in src/components/virality; the index route composes the scroll-based workspace.
- Use original React/D3-force graph presentation inspired by MiroFish, not copied AGPL source; example maps must be labeled as examples.
- Define visual tokens and motion in src/styles.css; honor reduced-motion preferences.
- Keep cursor-grid drawing on a pointer-transparent canvas with frame-based interpolation and cleaned-up listeners, avoiding React renders on pointer movement.
