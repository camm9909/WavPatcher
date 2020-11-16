# sh script
rm -rf build/
python3 setup.py py2app --packages=PIL
# ./dist/WavPatcher.app/Contents/MacOS/WavPatcher