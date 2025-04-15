import os

# Base directory for the project structure
base_dir = "flutter_file_tracker"

# Define the structure of the project
project_structure = {
    "lib": {
        "main.dart": "",
        "app": {
            "app.dart": "",
            "routes.dart": "",
            "themes.dart": ""
        },
        "core": {
            "utils": {
                "validators.dart": "",
                "file_helpers.dart": ""
            },
            "constants": {
                "app_constants.dart": ""
            }
        },
        "features": {
            "documents": {
                "data": {
                    "document_model.dart": "",
                    "document_repository.dart": ""
                },
                "presentation": {
                    "document_form.dart": "",
                    "document_list.dart": "",
                    "document_detail.dart": ""
                },
                "logic": {
                    "document_provider.dart": ""
                }
            }
        },
        "widgets": {
            "custom_button.dart": "",
            "file_upload_widget.dart": ""
        }
    },
    "pubspec.yaml": """
name: flutter_file_tracker
description: A Flutter app to track company files sent to clients.
version: 1.0.0+1

environment:
  sdk: ">=2.17.0 <3.0.0"

dependencies:
  flutter:
    sdk: flutter
  provider: ^6.0.5
  file_picker: ^5.2.5
  flutter_svg: ^1.1.5
  sqflite: ^2.2.0+3
  path_provider: ^2.0.11

flutter:
  uses-material-design: true
  assets:
    - assets/icons/
    - assets/images/
"""
}

# Helper function to create the project structure
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as file:
                file.write(content)

# Create the project structure
create_structure(base_dir, project_structure)

