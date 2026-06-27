"""Resource manager for MTN Cloud virtual images."""

from __future__ import annotations

from typing import Any

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.virtual_image import VirtualImage
from mtn_cloud.resources.base import BaseResource


class VirtualImagesResource(BaseResource[VirtualImage]):
    """
    Discover and manage virtual machine images.

    Virtual images are the templates used to provision instances. This
    includes both platform-provided OS images and custom images you have
    uploaded or imported.

    Example:
        # List all available images
        for img in cloud.virtual_images.list():
            print(f"{img.name}: {img.image_type}")

        # List only your custom (non-public) images
        custom = cloud.virtual_images.list(is_public=False)

        # Find an image by name
        ubuntu = cloud.virtual_images.get_by_name("Ubuntu 22.04")
    """

    _path = "/virtual-images"
    _model = VirtualImage
    _name = "virtual image"
    _list_key = "virtualImages"
    _item_key = "virtualImage"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        image_type: str | None = None,
        is_public: bool | None = None,
        **filters: Any,
    ) -> list[VirtualImage]:
        """
        List virtual images.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            phrase: Search phrase
            name: Filter by name
            image_type: Filter by image type (e.g. `"vmware"`, `"qcow2"`)
            is_public: If True, list only public images; if False, only private
            **filters: Additional filters

        Returns:
            List of virtual images
        """
        if name:
            filters["name"] = name
        if image_type:
            filters["imageType"] = image_type
        if is_public is not None:
            filters["filterType"] = "public" if is_public else "private"

        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, virtual_image_id: int) -> VirtualImage:
        """
        Get a virtual image by ID.

        Args:
            virtual_image_id: Virtual image ID

        Returns:
            Virtual image object
        """
        return super().get(virtual_image_id)

    def get_by_name(self, name: str) -> VirtualImage:
        """
        Get a virtual image by name.

        Args:
            name: Virtual image name

        Returns:
            Matching virtual image

        Raises:
            NotFoundError: If not found
        """
        images = self.list(phrase=name, max_results=25)
        for img in images:
            if img.name == name:
                return img
        raise NotFoundError(resource_type="VirtualImage", resource_id=name)

    def delete(self, virtual_image_id: int) -> bool:
        """
        Delete a virtual image.

        Only custom (user-uploaded) images can be deleted.

        Args:
            virtual_image_id: Virtual image ID

        Returns:
            True if deleted
        """
        return self._delete(virtual_image_id)
