#!/bin/bash
echo "🚀 Activating HFT Environment"
source venv/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
echo "✅ Ready to run HFT system"
echo ""
echo "Commands:"
echo "  python3 main.py --mode=dry    # Start Python layer"
echo "  ./init_pipeline.sh dry        # Start full system"
echo "  python3 test_macos.py         # Test system"
