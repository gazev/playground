
# crafting a user-agent
custom_agent:
	python -c "import urllib.request; opener = urllib.request.build_opener(); opener.addheaders = [('User-agent', '$(agent)/1.0')]; opener.open('http://localhost:8080')"

requests:
	python -c "import requests; requests.get('http://localhost:8080')"
