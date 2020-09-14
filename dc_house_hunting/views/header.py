
def view_with_header(view_callable):

    def wrapper(context):

        # Run view callable
        data=view_callable(context)

        request=context.request

        # Turn on the header
        data['show_header']=True

        return data

    return wrapper
