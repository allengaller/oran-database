# O-RAN 认证框架

## 概述
本文档为 O-RAN 系统提供全面的认证框架，涵盖多因素认证、证书管理和安全凭证处理。

## 认证架构

### 多因素认证 (MFA)
```yaml
mfa配置:
  主认证: "用户名密码"
  次级认证: 
    - "TOTP令牌"
    - "智能卡"
    - "生物识别验证"
  三级认证: "硬件安全模块"
  
认证级别:
  级别_1: "基本访问"
  级别_2: "管理访问" 
  级别_3: "根访问"
  级别_4: "安全管理"
```

### PKI 证书管理
```bash
#!/bin/bash
# O-RAN PKI 证书管理系统

# 证书颁发机构层次结构设置
setup_oran_ca() {
    echo "设置 O-RAN 证书颁发机构层次结构..."
    
    # 组织根 CA
    openssl req -x509 -newkey rsa:4096 -keyout root-ca-key.pem -out root-ca-cert.pem \
        -days 3650 -nodes -subj "/CN=O-RAN 根 CA/O=组织/C=CN"
    
    # 不同域的中间 CA
    for domain in management control user infrastructure; do
        openssl req -newkey rsa:2048 -keyout ${domain}-ca-key.pem -out ${domain}-ca-csr.pem \
            -nodes -subj "/CN=O-RAN ${domain^} CA/O=组织/C=CN"
        
        openssl x509 -req -in ${domain}-ca-csr.pem -out ${domain}-ca-cert.pem \
            -CA root-ca-cert.pem -CAkey root-ca-key.pem -CAcreateserial \
            -days 1825 -extfile ca-extensions.cnf
    done
}

# 组件证书颁发
issue_component_certificate() {
    local component_type=$1
    local component_name=$2
    local domain_ca=$3
    
    echo "为 ${component_type}/${component_name} 颁发证书"
    
    # 生成组件密钥对
    openssl genrsa -out ${component_name}-key.pem 2048
    
    # 创建证书签名请求
    openssl req -new -key ${component_name}-key.pem -out ${component_name}-csr.pem \
        -subj "/CN=${component_name}.${component_type}.oran.org/O=组织/C=CN"
    
    # 使用适当的域 CA 签名
    openssl x509 -req -in ${component_name}-csr.pem -out ${component_name}-cert.pem \
        -CA ${domain_ca}-ca-cert.pem -CAkey ${domain_ca}-ca-key.pem \
        -CAcreateserial -days 365 -extensions v3_req -extfile component-extensions.cnf
}
```

### OAuth 2.0 实现
```json
{
  "oauth2配置": {
    "授权服务器": "https://auth.oran.org",
    "令牌端点": "https://auth.oran.org/oauth2/token",
    "客户端注册": {
      "客户端ID": "oran-component-001",
      "客户端密钥": "生成的密钥",
      "重定向URI": [
        "https://near-rt-ric.oran.org/callback",
        "https://smo.oran.org/auth/callback"
      ],
      "授权类型": ["authorization_code", "client_credentials"],
      "响应类型": ["code"],
      "作用域": ["read", "write", "admin"]
    },
    "jwt配置": {
      "签名算法": "RS256",
      "令牌有效期": 3600,
      "刷新令牌有效期": 86400,
      "发行方": "https://auth.oran.org"
    }
  }
}
```

## 安全协议

### 双向 TLS 认证
```yaml
# O-RAN 接口的 mTLS 配置
mtls配置:
  e2接口:
    启用: true
    证书颁发机构: "控制平面-ca"
    需要客户端证书: true
    证书有效期: "730 天"
    吊销检查: "ocsp"
    密码套件:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
      - "TLS_AES_128_GCM_SHA256"
  
  f1接口:
    启用: true
    证书颁发机构: "用户平面-ca"
    需要客户端证书: true
    证书有效期: "365 天"
    吊销检查: "crl"
    密码套件:
      - "TLS_AES_128_GCM_SHA256"
      - "TLS_AES_256_GCM_SHA256"
```

### 会话管理
```python
# O-RAN 组件的安全会话管理
import hashlib
import secrets
from datetime import datetime, timedelta

class ORANSessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1小时
    
    def create_session(self, user_id, auth_level):
        """为认证用户创建安全会话"""
        session_id = secrets.token_urlsafe(32)
        session_token = hashlib.sha256(
            f"{user_id}:{session_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'auth_level': auth_level,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'session_token': session_token,
            'ip_address': self.get_client_ip()
        }
        
        return session_id, session_token
    
    def validate_session(self, session_id, session_token):
        """验证会话的真实性和新鲜度"""
        if session_id not in self.sessions:
            return False, "无效会话"
        
        session = self.sessions[session_id]
        
        # 检查令牌有效性
        expected_token = hashlib.sha256(
            f"{session['user_id']}:{session_id}:{session['created_at'].isoformat()}".encode()
        ).hexdigest()
        
        if session_token != expected_token:
            return False, "无效会话令牌"
        
        # 检查会话超时
        if datetime.utcnow() > session['last_activity'] + timedelta(seconds=self.session_timeout):
            del self.sessions[session_id]
            return False, "会话已过期"
        
        # 更新最后活动时间
        session['last_activity'] = datetime.utcnow()
        
        return True, "会话有效"
    
    def get_client_ip(self):
        """获取客户端IP地址（依赖实现）"""
        # 这通常来自请求头
        return "192.168.1.100"
```

## 最佳实践

### 凭证安全
- 使用强密码策略（最少12个字符，大小写混合，数字，符号）
- 使用 bcrypt 或 Argon2 进行密码哈希
- 启用每90天自动密码轮换
- 将凭证存储在加密保险库中（HashiCorp Vault、AWS Secrets Manager）
- 永远不要记录密码或敏感凭证

### 证书管理
- 定期证书轮换（根 CA 每年，中间 CA 每半年）
- 自动化证书续订流程
- 适当的证书吊销程序
- 证书透明度日志
- 使用硬件安全模块备份私钥

### 审计和监控
- 记录所有认证尝试（成功和失败）
- 监控异常认证模式
- 失败尝试后实施账户锁定
- 定期对认证系统进行安全审计
- 合规性报告以满足监管要求