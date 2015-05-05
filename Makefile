
help:
	@echo "to install everything: \n\t make install"
	@echo "to install just app: \n\t make install_app"
	@echo "to install just dependencies: \n\t make install_dep"
	@echo "to uninstall app: \n\t make uninstall"

install: install_dep install_app
	
install_app:
	sudo python setup.py install
	sudo cp ehfilemanager.desktop /usr/share/applications/ehfilemanager.desktop
	
install_dep: 
	sudo apt-get install python python-pip python-sqlite python-qt4 python-imaging python-yaml python-dateutil unrar-free
	sudo pip install requests beautifulsoup4 pylzma rarfile
	sudo apt-get install mcomix
	
uninstall:
	sudo pip uninstall eh-file-manager
	sudo rm /usr/share/applications/ehfilemanager.desktop
