<<<<<<< HEAD
window.PUBLIC_URL = '/';

window.config = {
  routerBasename: 'viewer/',
=======
window.PUBLIC_URL = '/viewer';

window.config = {
  routerBasename: '/viewer',
>>>>>>> edbf77cc96544880c2275055cd5a59758b37911a

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