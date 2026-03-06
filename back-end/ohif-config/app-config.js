window.config = {
  routerBasename: '/',

  showStudyList: true,

  extensions: [
    '@ohif/extension-default',
    '@ohif/extension-cornerstone',
  ],

  modes: [
    '@ohif/mode-longitudinal',
  ],

  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'dicomweb',
      configuration: {
        friendlyName: 'Orthanc',
        name: 'orthanc',

        qidoRoot: 'http://localhost:8082/dicom-web',
        wadoRoot: 'http://localhost:8082/dicom-web',
        wadoUriRoot: 'http://localhost:8082/wado',

        supportsFuzzyMatching: true,
        supportsWildcard: true,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
      },
    },
  ],

  defaultDataSourceName: 'dicomweb',
};