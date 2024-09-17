from .models import User
from rest_framework import serializers

class UserCreationSerializer(serializers.ModelSerializer):


    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    profession = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone1 = serializers.CharField(max_length=15)
    phone2 = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=1)
    date_of_birth = serializers.DateField()
    password = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name','last_name','profession','email','phone1','phone2','gender','date_of_birth','password','country','city']


    def validate(self,attrs):

        email_exists = User.objects.filter(email=attrs['email']).exists()

        if email_exists:
            raise serializers.ValidationError(detail="User with email already exits ")

        return super().validate(attrs)

    def create(self,validated_data):

        user = User.objects.create(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            profession = validated_data['profession'],
            email = validated_data['email'],
            phone1 = validated_data['phone1'],
            phone2 = validated_data['phone2'],
            is_active = True,
            gender = validated_data['gender'],
            date_of_birth =validated_data['date_of_birth'],
            country = validated_data['country'],
            city = validated_data['city']
        )

        user.set_password(validated_data['password'])

        user.save()

        return user

class UserDetailSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    profession = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone1 = serializers.CharField(max_length=15)
    phone2 = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=1)
    date_of_birth = serializers.DateField()
    password = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name','last_name','profession','email','phone1','phone2','gender','date_of_birth','password','country','city']

    def update(self, instance, validated_data):

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.profession = validated_data.get('profession', instance.profession)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.email = validated_data.get('email', instance.email)
        instance.phone1 = validated_data.get('phone1', instance.phone1)
        instance.phone2 = validated_data.get('phone2', instance.phone2)
        instance.dernier_diplome = validated_data.get('dernier_diplome', instance.dernier_diplome)
        instance.country = validated_data.get('country', instance.country)
        instance.city = validated_data.get('city', instance.city)

        password = validated_data.get('password', None)
        if password:
            # Assuming you have a method to hash passwords, replace `hash_password` with that
            instance.set_password(password)

        

        # Save the instance
        instance.save()
        return instance
