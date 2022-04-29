
def create_token(token_model, user, serializer):
    token, _ = token_model.objects.get_or_create(user=user)
    return token