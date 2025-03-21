import { ApolloClient, InMemoryCache } from "@apollo/client";

const client = new ApolloClient({
  uri: "http://127.0.0.1:8000/graphql",  // GraphQL 백엔드 주소 확인
  cache: new InMemoryCache(),
});

export default client;
