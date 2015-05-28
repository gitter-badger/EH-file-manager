
APTGET_RUN_DEP=python python-pip python-sqlite python-qt4 python-imaging python-yaml python-dateutil unrar-free mcomix
PIP_RUN_DEP=requests beautifulsoup4 pylzma rarfile

APTGET_BUILD_DEP=$(APTGET_RUN_DEP) python-qt4-dev
PIP_BUILD_DEP=$(PIP_RUN_DEP) pyinstaller

ARCH=$(shell arch)
VERSION=$(shell python -c "import ehfilemanager; print ehfilemanager.__version__")

help:
	@echo "Install everything: (Linux)\n\t make install"
	@echo "Install just app: (Linux)\n\t make install_app"
	@echo "Install just runtime dependencies: (Linux-Debian)\n\t make install_dep"
	@echo "Uninstall app: (Linux)\n\t make uninstall"
	@echo ""
	@echo "Build to static binary file: (Linux)\n\t make build"
	@echo "Get build dependencies: (Linux-Debian)\n\t make build_dep"

install: install_dep install_app
	
install_app: clean
	python setup.py build
	sudo python setup.py install
	sudo cp ehfilemanager.desktop /usr/share/applications/ehfilemanager.desktop
	
install_dep: 
	sudo apt-get install $(APTGET_RUN_DEP)
	sudo pip install $(PIP_RUN_DEP)
	
uninstall:
	sudo pip uninstall ehfilemanager
	sudo rm /usr/share/applications/ehfilemanager.desktop
	sudo rm -f /usr/local/bin/ehfilemanager
	
build_dep: 
	sudo apt-get install $(APTGET_BUILD_DEP)
	sudo pip install $(PIP_BUILD_DEP)
	
	$(eval PYINST_VER=$(shell python -c "import PyInstaller; v=PyInstaller.VERSION; print str(v[0])+str(v[1])") )
	$(eval PYINST_VER_DEV=$(shell python -c "import PyInstaller; v=PyInstaller.VERSION; print int('dev' in str(v))") )
	@echo "PyInstaller version: $(PYINST_VER), dev: $(PYINST_VER_DEV)"
	
	# PyInstaller requires version >= 2.2 OR dev
	# version 2.1 throws "import QtCore" error
	@if [ $(PYINST_VER_DEV) -ne 1 ] ; then \
		if [ ${PYINST_VER} -lt 22 ] ; then \
			echo "PyInstaller version is too low, installing development version from github";\
			make build_get_pyinstaller;\
		fi ;\
	fi
	
build_get_pyinstaller:
	sudo apt-get install git
	git clone https://github.com/pyinstaller/pyinstaller pyinstaller
	cd pyinstaller; python setup.py build
	cd pyinstaller; sudo python setup.py install
	sudo rm -rf pyinstaller

build: clean
	pyinstaller -F -n ehfilemanager ehfilemanager/__main__.py
	cp README* dist/ ; cp INSTALL* dist/ ; cp LICENSE* dist/ ; cp ehfilemanager.desktop dist/
	git archive --format tar --output ./dist/ehfilemanager_$(VERSION)_source.tar master
	cd dist; tar -zcvf ../ehfilemanager_$(VERSION)_Linux_$(ARCH).tar.gz *

clean:
	sudo rm -rf build dist eh_file_manager.egg-info
