"""
Figma API Client for extracting design data
"""

import requests
import json
import os
import ssl
import certifi
from typing import Dict, Any, Optional
from urllib3.util.ssl_ import create_urllib3_context


class FigmaClient:
    """Client for interacting with Figma API"""

    def __init__(self, access_token: str, verify_ssl: bool = True):
        """
        Initialize Figma client

        Args:
            access_token: Figma personal access token
            verify_ssl: Whether to verify SSL certificates
        """
        self.access_token = access_token
        self.base_url = "https://api.figma.com/v1"
        self.verify_ssl = verify_ssl
        self.headers = {
            "X-Figma-Token": access_token,
            "Content-Type": "application/json"
        }

        # Configure SSL context
        if verify_ssl:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        else:
            self.ssl_context = ssl._create_unverified_context()

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get Figma file data

        Args:
            file_id: Figma file ID

        Returns:
            Dict containing file data
        """
        url = f"{self.base_url}/files/{file_id}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=300
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Figma file: {str(e)}")

    def get_file_nodes(self, file_id: str, node_ids: list) -> Dict[str, Any]:
        """
        Get specific nodes from Figma file

        Args:
            file_id: Figma file ID
            node_ids: List of node IDs to fetch

        Returns:
            Dict containing node data
        """
        url = f"{self.base_url}/files/{file_id}/nodes"
        params = {"ids": ",".join(node_ids)}

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Figma nodes: {str(e)}")

    def get_images(self, file_id: str, node_ids: list, format: str = "png", scale: float = 1.0) -> Dict[str, Any]:
        """
        Get images of specific nodes

        Args:
            file_id: Figma file ID
            node_ids: List of node IDs
            format: Image format (png, jpg, svg, pdf)
            scale: Image scale factor

        Returns:
            Dict containing image URLs
        """
        url = f"{self.base_url}/images/{file_id}"
        params = {
            "ids": ",".join(node_ids),
            "format": format,
            "scale": scale
        }

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Figma images: {str(e)}")

    def extract_design_elements(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant design elements for BDD generation

        Args:
            file_data: Raw Figma file data

        Returns:
            Processed design data
        """
        processed_data = {
            "file_name": file_data.get("name", "Unknown"),
            "pages": [],
            "components": [],
            "text_elements": [],
            "interactive_elements": []
        }

        document = file_data.get("document", {})

        # Process pages
        for child in document.get("children", []):
            if child.get("type") == "CANVAS":
                page_data = {
                    "name": child.get("name"),
                    "id": child.get("id"),
                    "frames": []
                }

                # Process frames in the page
                for frame in child.get("children", []):
                    frame_data = self._process_frame(frame)
                    page_data["frames"].append(frame_data)

                processed_data["pages"].append(page_data)

        return processed_data

    def _process_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Figma frame and extract UI elements

        Args:
            frame: Frame data from Figma

        Returns:
            Processed frame data
        """
        frame_data = {
            "name": frame.get("name"),
            "id": frame.get("id"),
            "type": frame.get("type"),
            "elements": []
        }

        # Recursively process children
        for child in frame.get("children", []):
            element = self._process_element(child)
            if element:
                frame_data["elements"].append(element)

        return frame_data

    def _process_element(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process individual UI elements

        Args:
            element: Element data from Figma

        Returns:
            Processed element data or None
        """
        element_type = element.get("type")

        element_data = {
            "name": element.get("name"),
            "id": element.get("id"),
            "type": element_type,
            "visible": element.get("visible", True)
        }

        # Process different element types
        if element_type == "TEXT":
            element_data["text"] = element.get("characters", "")
            element_data["font_size"] = self._get_font_size(element)

        elif element_type in ["RECTANGLE", "ELLIPSE", "POLYGON"]:
            element_data["fills"] = element.get("fills", [])
            element_data["strokes"] = element.get("strokes", [])

        elif element_type == "COMPONENT" or element_type == "INSTANCE":
            element_data["component_id"] = element.get("componentId")

        # Check for interactive properties
        if element.get("interactions"):
            element_data["interactive"] = True
            element_data["interactions"] = element.get("interactions")

        # Process children recursively
        if element.get("children"):
            element_data["children"] = []
            for child in element["children"]:
                child_element = self._process_element(child)
                if child_element:
                    element_data["children"].append(child_element)

        return element_data

    def _get_font_size(self, text_element: Dict[str, Any]) -> Optional[float]:
        """
        Extract font size from text element

        Args:
            text_element: Text element from Figma

        Returns:
            Font size or None
        """
        style = text_element.get("style", {})
        return style.get("fontSize")
