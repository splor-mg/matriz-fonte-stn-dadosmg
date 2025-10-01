#!/usr/bin/env python3
"""
Script para publicar dados no portal CKAN usando Frictionless + API REST.
Baseado no script do dados-armazem-siafi-2025.
"""

import os
import sys
import argparse
import requests
from frictionless import Package
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description='Publicar dados no portal CKAN')
    parser.add_argument('--datapackage', default='datapackage.yaml', 
                       help='Caminho para o arquivo datapackage.yaml')
    parser.add_argument('--ckan-host', help='URL do CKAN (sobrescreve CKAN_HOST)')
    parser.add_argument('--ckan-key', help='Chave API do CKAN (sobrescreve CKAN_KEY)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Simular publicação sem enviar dados')
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get environment variables
    ckan_api_key = args.ckan_key or os.environ.get('CKAN_KEY')
    ckan_host = args.ckan_host or os.environ.get('CKAN_HOST')

    # Validate environment variables
    if not ckan_host:
        print("Error: CKAN_HOST not found in environment or .env file")
        print("Set CKAN_HOST environment variable or use --ckan-host")
        sys.exit(1)
    if not ckan_api_key:
        print("Error: CKAN_KEY not found in environment or .env file")
        print("Set CKAN_KEY environment variable or use --ckan-key")
        sys.exit(1)

    print(f"Using CKAN host: {ckan_host}")
    if args.dry_run:
        print("DRY RUN MODE - No data will be sent")

    try:
        # Load package
        package = Package(args.datapackage)
        print("Package loaded successfully")
        print(f"Package name: {package.name}")
        
        # Get package data
        package_data = package.to_dict()
        print(f"Organization: {package_data.get('owner_org', 'Not specified')}")
        
        if args.dry_run:
            print("Dry run - would publish the following data:")
            print(f"  Name: {package_data.get('name')}")
            print(f"  Title: {package_data.get('title')}")
            print(f"  Owner Org: {package_data.get('owner_org')}")
            print(f"  Resources: {len(package_data.get('resources', []))}")
            return
        
        # Prepare headers for CKAN API
        headers = {
            'Authorization': ckan_api_key,
            'Content-Type': 'application/json'
        }
        
        # First try to get the package to see if it exists
        get_url = f"{ckan_host}/api/3/action/package_show"
        response = requests.post(
            get_url,
            json={'id': package_data['name']},
            headers=headers
        )
        print(f"Checking if package exists: {response.status_code}")
        
        # Choose the appropriate endpoint based on whether the package exists
        if response.status_code == 200:
            print("Package exists, updating...")
            endpoint = f"{ckan_host}/api/3/action/package_update"
        else:
            print("Package doesn't exist, creating...")
            endpoint = f"{ckan_host}/api/3/action/package_create"
        
        # Send the request
        response = requests.post(
            endpoint,
            json=package_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("Package published successfully")
            result = response.json()
            if 'result' in result:
                print(f"Package ID: {result['result'].get('id', 'N/A')}")
                print(f"Package URL: {ckan_host}/dataset/{result['result'].get('name', 'N/A')}")
        else:
            print(f"Error response: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error publishing package: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
