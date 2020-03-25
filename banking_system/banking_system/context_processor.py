def user_detail_cp(request):
    if request.user.is_authenticated:
        return {'user_type': request.user.user_type}
    else:
        return {}
