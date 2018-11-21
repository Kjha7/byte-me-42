import React from 'react';

import { List, Card, Icon,Avatar,Button } from 'antd';

import axios from 'axios';



const IconText = ({ type, text }) => (
  <span>
    <Icon type={type} style={{ marginRight: 8 }} />
    {text}
  </span>
);

const Articles = (props) => {
  return (
  <div>
        <List
            itemLayout="vertical"
            size="medium"
            grid={{ gutter: 16, column: 2 }}
            //style={{ background: '#ECECEC', padding: '30px',alignItems: 'center',textAlign: 'center'}}
            dataSource={props.data}
            renderItem={item => (
            <List.Item
                key={item.title}
                style={{ background: '#ECECEC', padding: '20px',alignItems: 'center'}}
                extra={<img width={272} alt="logo" src="https://nonprofitorgs.files.wordpress.com/2010/07/blog.jpg" />}

            >
                <List.Item.Meta
                avatar={<Avatar src="http://www.sticomputer.com/newwebsite/wp-content/uploads/2018/03/Blog-Post-Icon-Navy-Blue-100x100.jpg" />}
                title={<a href={`/branch/${item.id}`}>{item.title}</a>}
                description={item.author}
              />
                {item.content}
            </List.Item>
          )}
        />
    </div>
    )

}

export default Articles;