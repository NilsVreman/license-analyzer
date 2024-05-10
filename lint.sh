SRC=${1:-.}

echo "Linting Target: $SRC"
echo "Running: flake8 --config=.flake8 $SRC"
flake8 --config=.flake8 $SRC

echo "Running: mypy $SRC"
mypy $SRC

echo "Running: pylint --recursive=true $SRC"
pylint --recursive=true $SRC

echo "Formatting Target: $SRC"
echo "Running: isort -c $SRC"
isort -c $SRC

echo "Running: black --check $SRC"
black --check $SRC
