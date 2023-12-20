import requests
from requests.exceptions import JSONDecodeError

def get_latest_npm(package_name):
    url = f"https://registry.npmjs.org/{package_name}/latest"
    response = requests.get(url)
    try:
        data = response.json()

        if 'version' not in data:
            return None
        else: return data['version']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None
def get_latest_composer(package_name):
    url = f"https://repo.packagist.org/p2/{package_name}.json"
    response = requests.get(url)
    try:
        data = response.json()
        if 'packages' not in data:
            return None
        else: return data['packages'][package_name][0]['version_normalized']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None
def get_latest_pip(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    try:
        data = response.json()
        if 'info' not in data:
            return None
        else: return data['info']['version']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None
def get_latest_ruby(package_name):
    url = f"https://rubygems.org/api/v1/versions/{package_name}/latest.json"
    response = requests.get(url)
    try:
        data = response.json()
        if 'version' not in data:
            return None
        else: return data['version']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None
def get_latest_golang(package_name):
    url = f"https://proxy.golang.org/{package_name}/@latest"
    response = requests.get(url)
    try:
        data = response.json()
        if 'Version' not in data:
            return None
        else: return data['Version']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None
def get_latest_maven(group_id, artifact_id):
    url = f"https://search.maven.org/solrsearch/select?q=g:%22{group_id}%22+AND+a:%22{artifact_id}%22&rows=1&wt=json"
    response = requests.get(url)
    try:
        data = response.json()

        if 'response' in data and 'docs' in data['response'] and len(data['response']['docs']) > 0:
            return data['response']['docs'][0]['latestVersion']
        else:
            return None
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {artifact_id}")
        return None
def get_latest_rust(package_name):
    url = f"https://crates.io/api/v1/crates/{package_name}"
    response = requests.get(url)
    try:
        data = response.json()
        if 'crate' not in data:
            return None
        else: return data['crate']['max_version']
    except JSONDecodeError:
        print(f"Error decoding JSON for package: {package_name}")
        return None