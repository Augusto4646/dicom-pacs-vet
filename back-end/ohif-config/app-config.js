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

        qidoRoot: 'https://orthanc.conexao46.com.br/dicom-web',
        wadoRoot: 'https://orthanc.conexao46.com.br/dicom-web',
        wadoUriRoot: 'https://orthanc.conexao46.com.br/wado',
      },
    },
  ],
};