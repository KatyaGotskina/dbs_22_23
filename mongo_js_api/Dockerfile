FROM node:16.20.2

WORKDIR /express_app

COPY package.json .
COPY package-lock.json .
RUN npm ci

COPY app.js .

CMD ["node", "app.js"]
