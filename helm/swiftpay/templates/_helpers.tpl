{{/*
Expand the name of the chart.
*/}}
{{- define "swiftpay.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "swiftpay.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "swiftpay.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "swiftpay.labels" -}}
helm.sh/chart: {{ include "swiftpay.chart" . }}
{{ include "swiftpay.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "swiftpay.selectorLabels" -}}
app.kubernetes.io/name: {{ include "swiftpay.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use for backend
*/}}
{{- define "swiftpay.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (printf "%s-%s" (include "swiftpay.fullname" .) "backend") .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use for frontend
*/}}
{{- define "swiftpay.frontendServiceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- printf "%s-%s" (include "swiftpay.fullname" .) "frontend" }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate certificates secret name
*/}}
{{- define "swiftpay.certificatesSecretName" -}}
{{- printf "%s-%s" (include "swiftpay.fullname" .) "swift-certs" }}
{{- end }}

{{/*
Generate TLS secret name
*/}}
{{- define "swiftpay.tlsSecretName" -}}
{{- printf "%s-%s" (include "swiftpay.fullname" .) "tls" }}
{{- end }}

{{/*
Database host
*/}}
{{- define "swiftpay.databaseHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-%s" .Release.Name "postgresql" }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "swiftpay.redisHost" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-%s-master" .Release.Name "redis" }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}