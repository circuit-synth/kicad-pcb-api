# [Number] - [Name]

## Purpose
[1-2 sentence description of what this reference demonstrates]

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. [Specific steps to create this reference]
4. Save as `project.kicad_pcb`

## File Contents
List of key elements in the PCB:
- [Element 1]
- [Element 2]
- [Element 3]
- ...

## Key S-expression Elements
S-expression tokens this reference tests:
- `(kicad_pcb ...)`
- `(footprint ...)`
- `(pad ...)`
- `(track ...)`
- `(via ...)`
- `(zone ...)`
- [Other relevant tokens]

## Expected Parser Behavior
- What properties should be extracted
- What should be preserved exactly
- What should be validated
- Any special handling needed

## Expected Formatter Behavior
- How it should be written back
- Any formatting requirements
- Indentation rules
- Token ordering

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- OR
- ⚠️ Semantic equivalence only (explain differences)

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify all elements parsed correctly
- [ ] Save to temporary file
- [ ] Load saved file
- [ ] Compare with original
- [ ] Verify round-trip fidelity

## Manufacturing Notes
- **JLCPCB Compatible**: Yes/No
- **Minimum trace width**: [value] mm
- **Minimum spacing**: [value] mm
- **Minimum via size**: [value] mm
- **Layer count**: [number]
- **Special requirements**: [any special considerations]

## Related References
Links to related reference files:
- See `[reference-number]` for [related feature]
- Build on `[reference-number]` by adding [feature]
- Compare with `[reference-number]` for [comparison]

## Known Issues
- [Any known parser/formatter issues]
- [KiCAD version differences]
- [Workarounds needed]
- [Future improvements]

## Visual Reference

[Optional: Add screenshot or description of what it looks like]

```
[ASCII art or simple diagram if helpful]
```

## Example Code

```python
import kicad_pcb_api as kpa

# Load this reference
pcb = kpa.load_pcb('reference-pcbs/.../project.kicad_pcb')

# Verify contents
assert len(pcb.footprints) == [expected]
assert len(pcb.tracks) == [expected]
assert len(pcb.vias) == [expected]

# Test round-trip
pcb.save('/tmp/test.kicad_pcb')
pcb2 = kpa.load_pcb('/tmp/test.kicad_pcb')
assert pcb.to_dict() == pcb2.to_dict()
```

## S-expression Sample

```lisp
(kicad_pcb
  (version 20240108)
  (generator "pcbnew")
  (general
    (thickness 1.6)
  )

  ; Key elements from this reference
  ; Add relevant snippets here
)
```

## Additional Notes
[Any other information relevant to this reference]
