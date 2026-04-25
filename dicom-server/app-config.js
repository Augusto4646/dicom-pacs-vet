window.config = {
  routerBasename: '/',
  extensions: [],
  modes: [],
  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'orthanc',
      configuration: {
        friendlyName: 'Orthanc',
        name: 'orthanc',
        wadoUriRoot: 'http://orthanc:8042/wado',
        qidoRoot: 'http://orthanc:8042/dicom-web',
        wadoRoot: 'http://orthanc:8042/dicom-web',
        supportsWildcard: true,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
      },
    },
  ],
};
