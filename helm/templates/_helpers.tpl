{{- define "open-payments-hub.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "open-payments-hub.fullname" -}}
{{- printf "%s" .Chart.Name -}}
{{- end -}}