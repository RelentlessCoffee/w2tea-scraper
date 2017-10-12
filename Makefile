.PHONY: deploy update

deploy:
	scp serve-prod tea-site:~/
	scp *.py tea-site:~/
	scp -r templates tea-site:~/
	ssh tea-site 'systemctl restart tea-site.service'

update:
	scp requirements.txt tea-site:~/
	ssh tea-site 'pip3 install -r requirements.txt'