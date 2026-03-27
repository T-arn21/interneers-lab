from rest_framework import serializers


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    category = serializers.CharField(max_length=120)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    brand = serializers.CharField(max_length=120)
    warehouse_quantity = serializers.IntegerField(min_value=0)

    def validate_name(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Name cannot be empty.")
        return cleaned

    def validate_category(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Category cannot be empty.")
        return cleaned

    def validate_brand(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Brand cannot be empty.")
        return cleaned

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value


class ProductUpdateSerializer(ProductCreateSerializer):
    name = serializers.CharField(max_length=120, required=False)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    category = serializers.CharField(max_length=120, required=False)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    brand = serializers.CharField(max_length=120, required=False)
    warehouse_quantity = serializers.IntegerField(min_value=0, required=False)

    # Soft-delete support for "update including deletion".
    deleted = serializers.BooleanField(required=False)

    def validate(self, attrs: dict) -> dict:
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": ["At least one field is required for update."]}
            )
        return attrs

