"""
This type stub file was generated by pyright.
"""

from django.http import FileResponse
from whitenoise.base import WhiteNoise

__all__ = ["WhiteNoiseMiddleware"]
class WhiteNoiseFileResponse(FileResponse):
    """
    Wrap Django's FileResponse to prevent setting any default headers. For the
    most part these just duplicate work already done by WhiteNoise but in some
    cases (e.g. the content-disposition header introduced in Django 3.0) they
    are actively harmful.
    """
    def set_headers(self, *args, **kwargs): # -> None:
        ...
    


class WhiteNoiseMiddleware(WhiteNoise):
    """
    Wrap WhiteNoise to allow it to function as Django middleware, rather
    than WSGI middleware.
    """
    def __init__(self, get_response=..., settings=...) -> None:
        ...
    
    def __call__(self, request): # -> WhiteNoiseFileResponse:
        ...
    
    @staticmethod
    def serve(static_file, request): # -> WhiteNoiseFileResponse:
        ...
    
    def add_files_from_finders(self): # -> None:
        ...
    
    def candidate_paths_for_url(self, url): # -> Generator[list[str] | str | Any, Any, None]:
        ...
    
    def immutable_file_test(self, path, url): # -> bool:
        """
        Determine whether given URL represents an immutable file (i.e. a
        file with a hash of its contents as part of its name) which can
        therefore be cached forever
        """
        ...
    
    def get_name_without_hash(self, filename):
        """
        Removes the version hash from a filename e.g, transforms
        'css/application.f3ea4bcc2.css' into 'css/application.css'

        Note: this is specific to the naming scheme used by Django's
        CachedStaticFilesStorage. You may have to override this if
        you are using a different static files versioning system
        """
        ...
    
    def get_static_url(self, name): # -> Any | None:
        ...
    


