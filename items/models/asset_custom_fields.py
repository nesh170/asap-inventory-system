from django.db import models

from items.models.asset_models import Asset


class AssetField(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=16, choices=[
        ('short_text', 'short-form text'), ('long_text', 'long-form text'),
        ('int', 'integer'), ('float', 'floating-point number')])
    private = models.BooleanField(default=False)

    def __str__(self):
        tag_string = "Asset Field {name} : {type} and Private:{private}".format
        return tag_string(name=self.name, type=self.type, private=self.private)


class IntAssetField(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='int_fields')
    field = models.ForeignKey(AssetField, on_delete=models.CASCADE, related_name='ints',
                              limit_choices_to={'type': 'int'})
    value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        tag_string = "Asset {asset_tag} - {field}:{value}".format
        return tag_string(field=self.field, value=self.value, asset_tag=self.asset.asset_tag)

    class Meta:
        unique_together = ('asset', 'field',)


class FloatAssetField(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='float_fields')
    field = models.ForeignKey(AssetField, on_delete=models.CASCADE, related_name='floats',
                              limit_choices_to={'type': 'float'})
    value = models.FloatField(null=True, blank=True)

    def __str__(self):
        tag_string = "Asset {asset_tag} - {field}:{value}".format
        return tag_string(field=self.field, value=self.value, asset_tag=self.asset.asset_tag)

    class Meta:
        unique_together = ('asset', 'field',)


class ShortTextAssetField(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='short_text_fields')
    field = models.ForeignKey(AssetField, on_delete=models.CASCADE, related_name='short_texts',
                              limit_choices_to={'type': 'short_text'})
    # RFC 2046, which defines the text/plain MIME type, is itself a 72 CPL plain text
    value = models.CharField(max_length=72, null=True, blank=True)

    def __str__(self):
        tag_string = "Asset {asset_tag} - {field}:{value}".format
        return tag_string(field=self.field, value=self.value, asset_tag=self.asset.asset_tag)

    class Meta:
        unique_together = ('asset', 'field',)


class LongTextAssetField(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='long_text_fields')
    field = models.ForeignKey(AssetField, on_delete=models.CASCADE, related_name='long_texts',
                              limit_choices_to={'type': 'long_text'})
    value = models.TextField(null=True, blank=True)

    def __str__(self):
        tag_string = "Asset {asset_tag} - {field}:{value}".format
        return tag_string(field=self.field, value=self.value, asset_tag=self.asset.asset_tag)

    class Meta:
        unique_together = ('asset', 'field',)