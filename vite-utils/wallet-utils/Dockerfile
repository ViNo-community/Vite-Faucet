FROM node:14.7.0

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY src ./src

ENTRYPOINT [ "npm", "run" ]