import { useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_HELLO, GET_HELLO_WITH_NAME } from './lib/queries';

function HelloWorld() {
  const { data, loading, error } = useQuery(GET_HELLO);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return <p>{data.hello}</p>;
}

function HelloWithName({ name }: { name: string }) {
  const { data, loading, error } = useQuery(GET_HELLO_WITH_NAME, {
    variables: { name },
    skip: !name,
  });

  if (!name) return null;
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return <p>{data.helloWithName}</p>;
}

export default function App() {
  const [inputName, setInputName] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setName(inputName);
  };

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: '600px', margin: '80px auto', padding: '0 20px' }}>
      <h1>GraphQL Hello World</h1>

      <section style={{ marginBottom: '40px' }}>
        <h2>기본 쿼리</h2>
        <HelloWorld />
      </section>

      <section>
        <h2>이름으로 인사하기</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input
            type="text"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            placeholder="이름을 입력하세요"
            style={{ padding: '8px 12px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <button
            type="submit"
            style={{ padding: '8px 16px', fontSize: '16px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            인사하기
          </button>
        </form>
        <HelloWithName name={name} />
      </section>
    </div>
  );
}
