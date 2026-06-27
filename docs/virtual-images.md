# Virtual Images

Use this guide to discover and manage VM images available for instance provisioning.

## What Are Virtual Images?

Virtual images are the templates used to provision instances. They include:
- Platform-provided OS images (Ubuntu, CentOS, Windows Server, etc.)
- Custom images you have uploaded or imported into your account

When you specify a type code like `MTN-CS10` in `instances.create()`, it maps to a virtual image under the hood. The `virtual_images` resource lets you browse available images and manage any custom ones you have uploaded.

## List Available Images

```python
from mtn_cloud import MTNCloud

cloud = MTNCloud(token="your-api-token")

images = cloud.virtual_images.list()
for img in images:
    print(f"{img.id}  {img.name}  type={img.image_type}  os={img.os_name}  public={img.is_public}")
```

## Filter by Public vs Custom

```python
# Platform-provided images only
public_images = cloud.virtual_images.list(is_public=True)

# Your custom images only
custom_images = cloud.virtual_images.list(is_public=False)
```

## Search by Name or Type

```python
# Search phrase (partial match)
ubuntu_images = cloud.virtual_images.list(phrase="Ubuntu")

# Exact name
img = cloud.virtual_images.get_by_name("Ubuntu 22.04 LTS")
print(img.id, img.image_type, img.os_code)
```

## Get by ID

```python
img = cloud.virtual_images.get(101)
print(img.name, img.min_disk, img.raw_size)
```

## Delete a Custom Image

Only user-uploaded (custom) images can be deleted. Platform-provided images cannot.

```python
cloud.virtual_images.delete(virtual_image_id=101)
```

## Notes

- `img.os_name` and `img.os_code` are convenience properties extracted from the nested `os_type` object.
- Images are used implicitly when you pass a type code to `instances.create()`. You do not need to reference a virtual image ID directly for standard provisioning.
- Custom image upload (import from URL or file) is done through the MTN Cloud Console under **Library → Virtual Images**.
