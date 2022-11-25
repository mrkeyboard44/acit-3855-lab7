FROM node:13.12.0-alpine

COPY . ./app

# Set working directory
WORKDIR /app

# Install app dependencies
RUN npm install
RUN npm install react-scripts@3.4.1 -g

# Add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# add app

# Start app
CMD ["npm", "start"]