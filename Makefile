.PHONY : render download clean
GITHUB_USER=Lioscro
GITHUB_REPO=info
GITHUB_BRANCH=master

PYTHON=python3

default:
	make download
	make render
	make clean

download:
	wget https://github.com/$(GITHUB_USER)/$(GITHUB_REPO)/archive/$(GITHUB_BRANCH).zip
	unzip master.zip $(GITHUB_REPO)-$(GITHUB_BRANCH)/assets/*
	mv $(GITHUB_REPO)-$(GITHUB_BRANCH)/assets assets

render:
	$(PYTHON) scripts/render.py --assets-dir assets --templates-dir templates --out-dir .

clean:
	rm -f master.zip
	rm -Rf $(GITHUB_REPO)-$(GITHUB_BRANCH)
	rm -Rf assets
