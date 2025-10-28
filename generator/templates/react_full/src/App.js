import React from 'react';

export default function App() {
  return (
    React.createElement('div', {style: {fontFamily: 'Arial, sans-serif', padding: '2rem'}}, [
      React.createElement('h1', null, 'Bem-vindo ao {{ project_name }}'),
      React.createElement('p', null, 'App React gerado automaticamente')
    ])
  );
}
