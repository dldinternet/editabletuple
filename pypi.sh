cd ~/app/editabletuple
rm -rf build/ dist/ editabletuple.egg-info/
python3 setup.py sdist bdist_wheel
twine upload dist/* && rm -rf build/ dist/ editabletuple.egg-info/
cd ..
