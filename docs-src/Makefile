all : \
	../docs/anydice-playground.svg \
	../docs/index.md \
	../docs/license.md \
	jupyterlite \
	playground

# These targets are names, not files. Make must always run them. A
# real file that must be rebuilt every time depends on FORCE instead.
.PHONY : all jupyterlite playground wheel FORCE
FORCE :

# The wheel file name contains the version, so no file target can name
# it. "jupyterlite" and "playground" both need the wheel. Make runs
# each target one time for each invocation, so this rule runs one
# time, even with "make -j".
wheel : FORCE
	cd .. && uv build --wheel

../docs/anydice-playground.svg : Makefile
	curl --fail --silent --show-error --location --output $@ 'https://img.shields.io/badge/%F0%9F%A4%B7%F0%9F%8E%B2%20AnyDice-Compatible%20%F0%9F%9B%9D-teal.svg'

../docs/index.md : ../README.md FORCE
	@set -eu; \
	raw_version=$$("$${PYTHON:-python3}" -c 'import importlib.metadata; print(importlib.metadata.version("dyceum"))'); \
	case "$$raw_version" in \
		*+*|*.dev*) git_ref=main; docs_version=latest; release=;; \
		*) git_ref="v$$raw_version"; docs_version=$$(printf '%s' "$$raw_version" | cut -d. -f1,2); release=1;; \
	esac; \
	temp_file=$$(mktemp ../docs/.index.md.XXXXXX); \
	trap 'rm -f "$$temp_file" "$$temp_file.release"' 0; \
	sed \
		-e '/<!-- docs:hide:start -->/,/<!-- docs:hide:end -->/d' \
		-e "s#raw.githubusercontent.com/posita/dyceum/main/#raw.githubusercontent.com/posita/dyceum/$$git_ref/#g" \
		-e "s#github.com/posita/dyceum/blob/main/#github.com/posita/dyceum/blob/$$git_ref/#g" \
		-e "s#github.com/posita/dyceum/tree/main/#github.com/posita/dyceum/tree/$$git_ref/#g" \
		-e "s#https://dyceum.org/latest/#https://dyceum.org/$$docs_version/#g" \
		../README.md > "$$temp_file"; \
	if [ -n "$$release" ]; then \
		sed -E \
			-e "s#(https://img\.shields\.io/pypi/[^/]+/dyceum)\.svg#\1/$$raw_version.svg#g" \
			-e "s#(https://pypi\.org/project/dyceum/)\)#\1$$raw_version/)#g" \
			"$$temp_file" > "$$temp_file.release"; \
		mv "$$temp_file.release" "$$temp_file"; \
	fi; \
	if ! cmp -s "$$temp_file" "$@"; then \
		chmod 644 "$$temp_file"; \
		mv "$$temp_file" "$@"; \
	fi

../docs/license.md : ../LICENSE
	cp $< $@

../docs/notebooks/%.ipynb : nb_%.py
	jupytext --to notebook --update $< --output $@
	ruff check --fix $@
	ruff format $@
	touch $@

# Zensical has no post-build hook. These rules assemble JupyterLite
# and the playground into docs/ before the site build. Git ignores
# both output directories.
jupyterlite : FORCE wheel ../docs/notebooks/dyceum_intro.ipynb
	@cd .. && set -eu; \
		dyceum_wheel=$$(ls -t dist/dyceum*-none-any.whl | head -n 1); \
		test -f "$$dyceum_wheel"; \
		set -- --piplite-wheels "$$dyceum_wheel"; \
		for url in $$("$${PYTHON:-python3}" docs-src/_uv_lock_wheels.py dyce lark optype ipywidgets jupyterlab-widgets widgetsnbextension); do \
			set -- "$$@" --piplite-wheels "$$url"; \
		done; \
		jupyter lite build --debug --output-dir docs/jupyter "$$@"

playground : FORCE wheel
	@cd .. && "$${PYTHON:-python3}" docs-src/assemble_playground.py docs/playground
