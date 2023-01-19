from rest_framework.renderers import JSONRenderer

class EmberJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
          "success": True,
          "codigo": status_code,
          "data": data,
          "mensaje":  "se obtuvo los datos"
        }

        if not str(status_code).startswith('2'):
            response["success"] = False
            response["data"] = None
            try:
                response["mensaje"] = data["detail"]
            except KeyError:
                response["mensaje"] = data
        return super(EmberJSONRenderer, self).render(response, accepted_media_type, renderer_context)