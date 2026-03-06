function OnStableStudy(studyId, tags, metadata)

  local study = ParseJson(RestApiGet('/studies/' .. studyId))

  local body = DumpJson({
    StudyInstanceUID = study["MainDicomTags"]["StudyInstanceUID"]
  })

  HttpPost(
    'http://django-docker:8000/api/webhook/novo-exame/',
    body,
    { ['Content-Type'] = 'application/json' }
  )

end