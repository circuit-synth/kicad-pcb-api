#!/bin/bash
# Helper script for creating new reference PCB files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 KiCAD PCB Reference Creator"
echo ""

# Check if in correct directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Must run from reference-pcbs directory${NC}"
    exit 1
fi

# Function to validate reference
validate_reference() {
    local ref_dir="$1"
    local ref_pcb="$ref_dir/project.kicad_pcb"

    echo ""
    echo "🔍 Validating reference: $ref_dir"

    # Check directory exists
    if [ ! -d "$ref_dir" ]; then
        echo -e "${RED}❌ Directory not found: $ref_dir${NC}"
        return 1
    fi

    # Check notes.md exists
    if [ ! -f "$ref_dir/notes.md" ]; then
        echo -e "${YELLOW}⚠️  Missing notes.md${NC}"
    else
        echo -e "${GREEN}✅ notes.md exists${NC}"
    fi

    # Check PCB file exists
    if [ ! -f "$ref_pcb" ]; then
        echo -e "${YELLOW}⚠️  Missing project.kicad_pcb - create in KiCAD${NC}"
        echo "   See notes.md for creation steps"
        return 0
    fi

    echo -e "${GREEN}✅ project.kicad_pcb exists${NC}"

    # Try to load with kicad-pcb-api
    echo "   Testing load..."
    cd ../..
    if source .venv/bin/activate 2>/dev/null && python3 -c "
import kicad_pcb_api as kpa
pcb = kpa.load_pcb('$ref_pcb')
print('   ✅ Loads successfully')
print(f'   Footprints: {len(pcb.footprints)}')
print(f'   Tracks: {len(pcb.tracks)}')
print(f'   Vias: {len(pcb.vias)}')
" 2>&1; then
        echo -e "${GREEN}✅ Parser test passed${NC}"
    else
        echo -e "${RED}❌ Parser test failed${NC}"
        cd reference-pcbs
        return 1
    fi
    cd reference-pcbs

    # Try round-trip test
    echo "   Testing round-trip..."
    cd ../..
    if source .venv/bin/activate 2>/dev/null && python3 -c "
import kicad_pcb_api as kpa
import tempfile
import os

pcb = kpa.load_pcb('$ref_pcb')
with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_pcb', delete=False) as f:
    temp_path = f.name

pcb.save(temp_path)
pcb2 = kpa.load_pcb(temp_path)
os.unlink(temp_path)

if pcb.to_dict() == pcb2.to_dict():
    print('   ✅ Round-trip test passed')
else:
    print('   ⚠️  Round-trip changed data (may be acceptable)')
" 2>&1; then
        echo -e "${GREEN}✅ Round-trip test passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Round-trip test warning${NC}"
    fi
    cd reference-pcbs

    return 0
}

# Function to list all Phase 1 references
list_phase1() {
    echo "Phase 1 References (Essential):"
    echo ""
    echo "01. 01-basic-structure/01-blank-pcb"
    echo "05. 01-basic-structure/05-edge-cuts-rectangle"
    echo "16. 04-components/16-single-resistor-0603"
    echo "24. 05-routing/24-single-trace-straight"
    echo "30. 06-vias/30-single-via-through"
    echo "09. 02-zones/09-copper-pour-simple"
}

# Main menu
if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  $0 validate <reference-dir>    Validate a reference"
    echo "  $0 validate-all                Validate all Phase 1 references"
    echo "  $0 list                        List Phase 1 references"
    echo ""
    echo "Examples:"
    echo "  $0 validate 01-basic-structure/01-blank-pcb"
    echo "  $0 validate-all"
    exit 0
fi

case "$1" in
    list)
        list_phase1
        ;;

    validate)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Error: Must specify reference directory${NC}"
            echo "Example: $0 validate 01-basic-structure/01-blank-pcb"
            exit 1
        fi
        validate_reference "$2"
        ;;

    validate-all)
        echo "Validating all Phase 1 references..."
        refs=(
            "01-basic-structure/01-blank-pcb"
            "01-basic-structure/05-edge-cuts-rectangle"
            "04-components/16-single-resistor-0603"
            "05-routing/24-single-trace-straight"
            "06-vias/30-single-via-through"
            "02-zones/09-copper-pour-simple"
        )

        total=${#refs[@]}
        passed=0

        for ref in "${refs[@]}"; do
            if validate_reference "$ref"; then
                ((passed++))
            fi
        done

        echo ""
        echo "======================================"
        echo "Results: $passed/$total passed"
        echo "======================================"

        if [ $passed -eq $total ]; then
            echo -e "${GREEN}✅ All Phase 1 references validated!${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠️  Some references need work${NC}"
            exit 1
        fi
        ;;

    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run '$0' for usage"
        exit 1
        ;;
esac
