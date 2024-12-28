import json
from .models import Field
from .serializers import FieldSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from .forms.init_field import InitFieldForm


class FieldViewSet(ModelViewSet):
    serializer_class = FieldSerializer
    queryset = Field.objects.select_related('created_by')
    
    @action(detail=False,methods=['post'])
    def init_field_request(self,request, *args, **kwargs):
        form = InitFieldForm(json.loads(request.body))
        
        if form.is_valid():  
            for period in ['SPRING','WINTER','SUMMER','AUTUMN'] :
                if  form.data.get('period') in period:
                    form.data['period'] = period
                    
            #process AI field pre-creation suggestions  
            return Response(form.data)
            
        return Response(dict(form.errors),status=402)
    

        

