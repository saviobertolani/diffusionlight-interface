import json
import os
from typing import Dict, Any

class DiffusionLightWorkflow:
    """Workflow configuration for DiffusionLight on RunPod"""
    
    def __init__(self):
        self.workflow_template = self._load_workflow_template()
    
    def _load_workflow_template(self) -> Dict[str, Any]:
        """Load the base DiffusionLight workflow template"""
        workflow_path = os.path.join(
            os.path.dirname(__file__), 
            '../../workflows/diffusionlight-workflow.json'
        )
        
        try:
            with open(workflow_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return a simplified workflow template if file not found
            return self._get_default_workflow()
    
    def _get_default_workflow(self) -> Dict[str, Any]:
        """Default workflow template for DiffusionLight"""
        return {
            "1": {
                "inputs": {
                    "image": "input_image_url",
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "2": {
                "inputs": {
                    "image": ["1", 0]
                },
                "class_type": "ChromeballMask",
                "_meta": {
                    "title": "Chromeball Mask"
                }
            },
            "3": {
                "inputs": {
                    "image": ["1", 0],
                    "mask": ["2", 0]
                },
                "class_type": "Ball2Envmap",
                "_meta": {
                    "title": "Ball to Environment Map"
                }
            },
            "4": {
                "inputs": {
                    "image": ["3", 0],
                    "exposure_stops": 2.0
                },
                "class_type": "ExposureBracket",
                "_meta": {
                    "title": "Exposure Bracket"
                }
            },
            "5": {
                "inputs": {
                    "images": ["4", 0]
                },
                "class_type": "Exposure2HDR",
                "_meta": {
                    "title": "Exposure to HDR"
                }
            },
            "6": {
                "inputs": {
                    "image": ["5", 0],
                    "filename_prefix": "diffusionlight_result",
                    "format": "hdr"
                },
                "class_type": "SaveHDR",
                "_meta": {
                    "title": "Save HDR"
                }
            }
        }
    
    def create_workflow(self, input_image_url: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customized workflow based on configuration"""
        workflow = self.workflow_template.copy()
        
        # Update input image
        if "1" in workflow:
            workflow["1"]["inputs"]["image"] = input_image_url
        
        # Apply configuration
        preset = configuration.get('preset', 'automotivo')
        resolution = configuration.get('resolution', 1024)
        output_format = configuration.get('output_format', 'hdr')
        anti_aliasing = configuration.get('anti_aliasing', '4')
        
        # Preset-specific configurations
        preset_configs = {
            'automotivo': {
                'exposure_stops': 2.5,
                'tone_mapping': 'automotive',
                'saturation': 1.2
            },
            'produto': {
                'exposure_stops': 2.0,
                'tone_mapping': 'product',
                'saturation': 1.0
            },
            'arquitetonico': {
                'exposure_stops': 3.0,
                'tone_mapping': 'architectural',
                'saturation': 0.9
            }
        }
        
        preset_config = preset_configs.get(preset, preset_configs['automotivo'])
        
        # Update workflow nodes based on configuration
        self._update_exposure_bracket(workflow, preset_config['exposure_stops'])
        self._update_output_settings(workflow, output_format, resolution)
        self._update_quality_settings(workflow, anti_aliasing)
        
        return workflow
    
    def _update_exposure_bracket(self, workflow: Dict[str, Any], exposure_stops: float):
        """Update exposure bracket settings"""
        if "4" in workflow:
            workflow["4"]["inputs"]["exposure_stops"] = exposure_stops
    
    def _update_output_settings(self, workflow: Dict[str, Any], output_format: str, resolution: int):
        """Update output format and resolution settings"""
        if "6" in workflow:
            workflow["6"]["inputs"]["format"] = output_format
            
        # Add resolution node if needed
        if resolution != 1024:
            workflow["7"] = {
                "inputs": {
                    "image": ["5", 0],
                    "width": resolution,
                    "height": resolution // 2
                },
                "class_type": "ImageScale",
                "_meta": {
                    "title": "Scale Image"
                }
            }
            # Update save node to use scaled image
            workflow["6"]["inputs"]["image"] = ["7", 0]
    
    def _update_quality_settings(self, workflow: Dict[str, Any], anti_aliasing: str):
        """Update quality and anti-aliasing settings"""
        # Add anti-aliasing configuration to relevant nodes
        aa_multiplier = {
            '1': 1,
            '2': 2,
            '4': 4,
            '8': 8
        }.get(anti_aliasing, 4)
        
        # Update nodes that support anti-aliasing
        for node_id, node in workflow.items():
            if node.get('class_type') in ['Ball2Envmap', 'Exposure2HDR']:
                if 'inputs' not in node:
                    node['inputs'] = {}
                node['inputs']['anti_aliasing'] = aa_multiplier

class RunPodWorkflowManager:
    """Manager for RunPod workflow operations"""
    
    def __init__(self):
        self.workflow_generator = DiffusionLightWorkflow()
    
    def prepare_runpod_payload(self, input_image_url: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare complete payload for RunPod submission"""
        
        # Generate workflow
        workflow = self.workflow_generator.create_workflow(input_image_url, configuration)
        
        # Prepare RunPod payload
        payload = {
            "input": {
                "workflow": workflow,
                "images": [
                    {
                        "name": "input_image_url",
                        "image": input_image_url
                    }
                ],
                "webhook": {
                    "url": os.getenv('WEBHOOK_URL'),
                    "method": "POST",
                    "headers": {
                        "Authorization": f"Bearer {os.getenv('WEBHOOK_SECRET', 'default-secret')}"
                    }
                },
                "output_settings": {
                    "return_temp_images": True,
                    "return_workflow_outputs": True,
                    "output_format": configuration.get('output_format', 'hdr'),
                    "quality": "high"
                }
            }
        }
        
        return payload
    
    def validate_configuration(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize configuration"""
        validated = {}
        
        # Preset validation
        valid_presets = ['automotivo', 'produto', 'arquitetonico']
        validated['preset'] = configuration.get('preset', 'automotivo')
        if validated['preset'] not in valid_presets:
            validated['preset'] = 'automotivo'
        
        # Resolution validation
        valid_resolutions = [512, 1024, 2048]
        validated['resolution'] = int(configuration.get('resolution', 1024))
        if validated['resolution'] not in valid_resolutions:
            validated['resolution'] = 1024
        
        # Output format validation
        valid_formats = ['hdr', 'exr', 'npy']
        validated['output_format'] = configuration.get('output_format', 'hdr')
        if validated['output_format'] not in valid_formats:
            validated['output_format'] = 'hdr'
        
        # Anti-aliasing validation
        valid_aa = ['1', '2', '4', '8']
        validated['anti_aliasing'] = str(configuration.get('anti_aliasing', '4'))
        if validated['anti_aliasing'] not in valid_aa:
            validated['anti_aliasing'] = '4'
        
        return validated
    
    def estimate_processing_time(self, configuration: Dict[str, Any]) -> int:
        """Estimate processing time in seconds based on configuration"""
        base_time = 60  # 1 minute base
        
        # Resolution factor
        resolution = configuration.get('resolution', 1024)
        resolution_factor = {
            512: 0.5,
            1024: 1.0,
            2048: 2.5
        }.get(resolution, 1.0)
        
        # Anti-aliasing factor
        aa = configuration.get('anti_aliasing', '4')
        aa_factor = {
            '1': 0.7,
            '2': 1.0,
            '4': 1.5,
            '8': 2.5
        }.get(aa, 1.5)
        
        # Format factor
        format_factor = {
            'hdr': 1.0,
            'exr': 1.3,
            'npy': 0.8
        }.get(configuration.get('output_format', 'hdr'), 1.0)
        
        estimated_time = int(base_time * resolution_factor * aa_factor * format_factor)
        return max(estimated_time, 30)  # Minimum 30 seconds

