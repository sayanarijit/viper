## Contributing to Viper

To contribute to this project, first fork this project in your own GitHub account
and clone that forked repo locally with `git clone`.

It's recommended to activate a [Virtual Environment](https://docs.python.org/3/tutorial/venv.html)

Then inside the project directory run the followiing commands:

```bash
# Install dev dependencies and hooks
make install

# Make the changes

# Generate docs (README.md)
make docs

# Run black and lint checks
make checks

# Run unit tests
make unit-tests

# Run all the tests
make tests
```

Then commit push the changes to a new branch named something like
`fix/some-tests`, `add/new-improvements`, `cleanup/removed-unused` etc.


Then open a pull request to the Viper master branch.
