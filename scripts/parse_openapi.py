#!/usr/bin/env python3
"""
Parse CODING OpenAPI YAML and generate Python SDK code
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_python_type(schema: Dict[str, Any], definitions: Dict[str, Any]) -> str:
    """Convert OpenAPI type to Python type hint"""
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return ref_name
    
    type_name = schema.get("type", "Any")
    
    if type_name == "string":
        return "str"
    elif type_name == "integer":
        return "int"
    elif type_name == "number":
        return "float"
    elif type_name == "boolean":
        return "bool"
    elif type_name == "array":
        item_type = get_python_type(schema.get("items", {}), definitions)
        return f"List[{item_type}]"
    elif type_name == "object":
        return "Dict[str, Any]"
    else:
        return "Any"


def extract_operations(yaml_file: Path) -> Dict[str, Any]:
    """Extract API operations from OpenAPI YAML"""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    operations = {}
    paths = spec.get("paths", {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ["post", "get", "put", "delete"]:
                continue
            
            operation_id = details.get("operationId")
            if not operation_id:
                continue
            
            # Extract request schema
            request_schema = {}
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                json_content = content.get("application/json", {})
                request_schema = json_content.get("schema", {})
            
            # Extract response schema
            response_schema = {}
            responses = details.get("responses", {})
            if "200" in responses:
                response_content = responses["200"].get("content", {})
                json_content = response_content.get("application/json", {})
                response_schema = json_content.get("schema", {})
            
            operations[operation_id] = {
                "path": path,
                "method": method.upper(),
                "description": details.get("description", ""),
                "summary": details.get("summary", ""),
                "request_schema": request_schema,
                "response_schema": response_schema,
                "parameters": details.get("parameters", []),
            }
    
    return operations


def generate_model_from_schema(model_name: str, schema: Dict[str, Any]) -> str:
    """Generate Pydantic model from schema"""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields = []
    for prop_name, prop_schema in properties.items():
        python_type = get_python_type(prop_schema, {})
        is_required = prop_name in required
        
        # Format field
        optional_suffix = "" if is_required else " = None"
        description = prop_schema.get("description", "")
        
        if description:
            field_line = f'    {camel_to_snake(prop_name)}: {python_type}{optional_suffix}  # {description}'
        else:
            field_line = f'    {camel_to_snake(prop_name)}: {python_type}{optional_suffix}'
        
        fields.append(field_line)
    
    fields_str = "\n".join(fields) if fields else "    pass"
    
    return f"""class {model_name}(BaseModel):
    \"\"\"Auto-generated model\"\"\"
{fields_str}
"""


def generate_api_methods(operations: Dict[str, Any]) -> str:
    """Generate async API methods"""
    methods = []
    
    for operation_id, op_details in sorted(operations.items()):
        description = op_details.get("description", "").replace("\n", " ").strip()
        summary = op_details.get("summary", "").strip()
        
        # Extract request parameters
        request_props = op_details["request_schema"].get("properties", {})
        request_params = []
        
        for param_name, param_schema in request_props.items():
            python_type = get_python_type(param_schema, {})
            snake_name = camel_to_snake(param_name)
            is_required = param_name in op_details["request_schema"].get("required", [])
            
            if is_required:
                request_params.append(f"        {snake_name}: {python_type},")
            else:
                request_params.append(f"        {snake_name}: Optional[{python_type}] = None,")
        
        request_params_str = "\n".join(request_params) if request_params else ""
        
        # Build request dict
        request_dict_items = []
        for param_name in request_props.keys():
            snake_name = camel_to_snake(param_name)
            request_dict_items.append(f'            "{param_name}": {snake_name},')
        
        request_dict_str = "\n".join(request_dict_items) if request_dict_items else ""
        
        # Generate method signature
        method_doc = f'    async def {camel_to_snake(operation_id)}(\n        self,\n{request_params_str}\n    ) -> Dict[str, Any]:'
        
        # Generate method body
        method_body = f'''
        \"\"\"
        {summary or description}
        
        {description if description != summary else ""}
        \"\"\"
        payload = {{
{request_dict_str}
        }}
        # Remove None values
        payload = {{k: v for k, v in payload.items() if v is not None}}
        return await self._request("{operation_id}", **payload)
'''
        
        methods.append(method_doc + method_body)
    
    return "\n".join(methods)


def generate_sdk(yaml_file: Path, output_dir: Path):
    """Generate complete SDK"""
    print(f"📖 解析 {yaml_file}...")
    operations = extract_operations(yaml_file)
    print(f"✅ 找到 {len(operations)} 个 API 操作")
    
    # Generate API methods
    api_methods = generate_api_methods(operations)
    
    # Update client.py with generated methods
    client_file = output_dir / "src" / "coding_sdk" / "client_generated.py"
    
    client_code = f'''"""Auto-generated API methods for CODING SDK"""

from typing import Any, Dict, Optional


GENERATED_METHODS = """
{api_methods}
"""

# 说明：将下面的方法复制到 client.py 中的 CodingClient 类

{api_methods}
'''
    
    client_file.parent.mkdir(parents=True, exist_ok=True)
    client_file.write_text(client_code, encoding='utf-8')
    print(f"✅ 生成的 API 方法已保存到 {client_file}")
    
    # Generate summary
    summary_file = output_dir / "API_METHODS.md"
    summary = "# CODING API 方法列表\n\n"
    
    for operation_id, op_details in sorted(operations.items()):
        summary += f"## `{camel_to_snake(operation_id)}`\n\n"
        summary += f"**描述**: {op_details.get('description', op_details.get('summary', 'N/A'))}\n\n"
        
        if op_details["request_schema"].get("properties"):
            summary += "**参数**:\n\n"
            for prop_name, prop_schema in op_details["request_schema"]["properties"].items():
                py_type = get_python_type(prop_schema, {})
                required = prop_name in op_details["request_schema"].get("required", [])
                req_mark = "✅" if required else "❌"
                summary += f"- `{camel_to_snake(prop_name)}` ({py_type}) {req_mark} - {prop_schema.get('description', '')}\n"
            summary += "\n"
        
        summary += "---\n\n"
    
    summary_file.write_text(summary, encoding='utf-8')
    print(f"✅ API 文档已保存到 {summary_file}")


if __name__ == "__main__":
    yaml_file = Path("docs/openapi_ref/document.yaml")
    output_dir = Path(".")
    
    if not yaml_file.exists():
        print(f"❌ 找不到 {yaml_file}")
        exit(1)
    
    generate_sdk(yaml_file, output_dir)
    print("\n🎉 SDK 生成完成！")
    print("📝 查看 client_generated.py 获取所有 API 方法")
    print("📖 查看 API_METHODS.md 获取 API 文档")
