# -*- coding: utf-8 -*-
import json, os
import datetime
import argparse
import dicttoxml
import subprocess
import xml.etree.ElementTree as ET
# import shutil
from xml.dom.minidom import parseString

from Parsers.conanParser import conanParser
from Parsers.dartParser import dartParser
from Parsers.dotnetParser import dotnetParser
from Parsers.gradleGroovyParser import gradleGroovyParser
from Parsers.gradlekotlinDSLParser import gradlekotlinDSLParser
from Parsers.mavenParser import mavenParser
from Parsers.npmParser import npmParser
from Parsers.phpParser import phpParser
from Parsers.rustParser import rustParser
from Parsers.swiftParser import swiftParser
from Parsers.yarnParser import YarnParser
from Parsers.rubyParser import rubyparser
from Parsers.requirementsParser import requirementsParser
from Parsers.gomodParser import goModParser
from Utility.helpers import get_project_path
from Utility.dependencyTree import DependencyTree
from Utility.zip import zip_extract
from Utility.checkVersion import *

def createSbom(path, output_path, checkFlag):
    projname = os.path.split(path)[-1]
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": "1",
        "metadata": {
            "timestamp": datetime.datetime.now().isoformat(),
            "component": {
                "group": "",
                "name": projname,
                "version": "0.0.0",
                "type": "application",
            },
        },
        "components": [],
        "services": [],
        "dependencies": [],
    }

    phpParser(path, sbom)
    npmParser(path, sbom)
    YarnParser(path, sbom)
    requirementsParser(path, sbom)
    conanParser(path, sbom)
    dartParser(path, sbom)
    dotnetParser(path, sbom)
    gradleGroovyParser(path, sbom)
    gradlekotlinDSLParser(path, sbom)
    mavenParser(path, sbom)
    rustParser(path, sbom)
    swiftParser(path, sbom)
    rubyparser(path,sbom)
    goModParser(path,sbom)
    versionJson = {}
    if checkFlag:
        for component in sbom["components"]:
            if component["purl"].split("/")[0] == "pkg:npm":
                ver = get_latest_npm(component["name"])
                if (component["version"] != ver ) and (ver != None):
                    versionJson[component["name"]] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0] == "pkg:composer":
                ver = get_latest_composer(f"{component["group"]}/{component["name"]}")
                if (component["version"] != ver ) and (ver != None):
                    versionJson[f"{component["group"]}/{component["name"]}"] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0] == "pkg:pypi":
                ver = get_latest_pip(component["name"])
                if (component["version"] != ver ) and (ver != None):
                    versionJson[component["name"]] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0] == "pkg:gem":
                ver = get_latest_ruby(component["name"])
                if (component["version"] != ver ) and (ver != None):
                    versionJson[component["name"]] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0] == "pkg:golang":
                ver = get_latest_golang(f"{component["group"]}/{component["name"]}")
                if (component["version"] != ver ) and (ver != None):
                    # print(f"{component["group"]}/{component["name"]}:\n  current \t latest")
                    # print(f"⚠️{component["version"]} \t {ver}")
                    versionJson[f"{component["group"]}/{component["name"]}"] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0]=="pkg:maven":
                ver = get_latest_maven(component["group"],component["name"])
                if (component["version"] != ver ) and (ver != None):
                    versionJson[f"{component["group"]}/{component["name"]}"] = {"current":component["version"], "latest":ver}
            elif component["purl"].split("/")[0]=="pkg:rust":
                ver = get_latest_rust(component["name"])
                if (component["version"] != ver ) and (ver != None):
                    versionJson[component["name"]] = {"current":component["version"], "latest":ver}

        with open(os.path.join(os.path.dirname(output_path), 'version.json'), 'w') as f:
            json.dump(versionJson, f, indent=4)

    return sbom

def createsbomJson(path, checkFlag):
    output_path=os.path.join(path,'sbom.json')
    if(os.path.split(path)[-1].split('.')[-1] == 'zip'):
        output_path=os.path.join(os.path.dirname(path),'sbom.json')
        path=zip_extract(path)
    sbom = createSbom(path, output_path, checkFlag)
    print(output_path)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(sbom, file, indent=4)

        file.close()
    return sbom


def createsbomXML(path, checkFlag):
    output_path=os.path.join(path,'sbom.xml')
    if(os.path.split(path)[-1].split('.')[-1] == 'zip'):
        output_path=os.path.join(os.path.dirname(path),'sbom.xml')
        path=zip_extract(path)
    sbom = createSbom(path, output_path, checkFlag)
    xmlStr = dicttoxml.dicttoxml(sbom)
    dom = parseString(xmlStr)
    prettyXML = dom.toprettyxml()
    with open(output_path, "w") as file:
        file.write(prettyXML)
    return sbom

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Software Bill of Materials (SBOM) for a project.')

    parser.add_argument('-p', '--project_path', type=str, help='The path to the project')
    parser.add_argument('-f', '--format', type=str, help='The output file format')
    parser.add_argument('--vul', action='store_true', help='Include vulnerability information (yes/no)')
    parser.add_argument('--tree', action='store_true', help='Generate dependency tree (yes/no)')
    parser.add_argument('--check', action='store_true', help='check for new versions (yes/no)')
    sbom={}
    args = parser.parse_args()
    output_file=''
    user_input_report=''
    treeFlag=False
    checkFlag = False
    if args.project_path:
        user_input_path = args.project_path
        if not os.path.isabs(user_input_path):
            user_input_path = os.path.join(os.getcwd(), user_input_path)

        project_path = user_input_path
    else:
        project_path, output_file, user_input_report, treeFlag, checkFlag= get_project_path()
        output_file = f"sbom.{output_file}"
    project_path = os.path.abspath(project_path)
    if(output_file==""):
        if args.format:
            if args.format not in ['xml', 'json'] or args.format == 'json':
                if args.format not in ['xml','json']: 
                    print('Invalid output format\n\nGenerating in json')
                    output_file = 'sbom.json'
                else :
                    output_file = f'sbom.{args.format}'
            
        else:
            output_file = 'sbom.json'
    if args.check or checkFlag:
        checkFlag = True

    print("\n🚀 Generating SBOM...")
    if output_file=='sbom.json':
        sbom=createsbomJson(project_path, checkFlag)
    else:
        sbom = createsbomXML(project_path,checkFlag)
    zipFlag=False
    if(os.path.split(project_path)[-1].split('.')[-1] == 'zip'):
        # shutil.rmtree(os.path.join(os.path.split(project_path)[0], os.path.splitext(os.path.basename(project_path))[0]), ignore_errors=True)
        project_path=os.path.dirname(project_path)
        zipFlag=True
    if args.tree or treeFlag:
        DependencyTree(sbom, project_path)
    print(f"\n✅ SBOM generated successfully!")
    print(f"📄 SBOM file is located at: {os.path.join(project_path, output_file)}")
    if args.vul or user_input_report=='yes':
        subprocess.run(["depscan", "--bom", os.path.join(project_path, output_file), "-o", os.path.join(project_path, "Report.html")], shell=True)
        print(f"\n✅ Vulnerability Report generated successfully, Please take the necessary actions")

