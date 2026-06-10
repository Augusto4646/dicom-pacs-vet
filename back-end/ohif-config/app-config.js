window.PUBLIC_URL = '/';

window.config = {
  routerBasename: 'viewer/',

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

        wadoUriRoot: "/orthanc/wado",
        qidoRoot: "/orthanc/dicom-web",
        wadoRoot: "/orthanc/dicom-web",
      },
    },
  ],
};