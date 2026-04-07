import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';

const typeDefs = `#graphql
  type Query {
    hello: String!
    helloWithName(name: String!): String!
  }
`;

const resolvers = {
  Query: {
    hello: () => 'Hello, World!',
    helloWithName: (_: unknown, { name }: { name: string }) =>
      `Hello, ${name}!`,
  },
};

async function main() {
  const server = new ApolloServer({ typeDefs, resolvers });

  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
    context: async ({ req }) => ({
      headers: req.headers,
    }),
  });

  console.log(`🚀 Server ready at ${url}`);
}

main();
