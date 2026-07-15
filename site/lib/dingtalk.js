import axios from 'axios';

// 钉钉 OAuth2 + topapi 接口封装。
// 移植自 houpe-auth/dingtalk.js，改为 ESM 工厂注入凭证，便于测试。
export function createDingtalk({ appKey, appSecret } = {}) {
  let tokenCache = { token: null, expires: 0 };

  async function getAccessToken() {
    const now = Date.now();
    if (tokenCache.token && tokenCache.expires > now) return tokenCache.token;

    const { data } = await axios.get('https://oapi.dingtalk.com/gettoken', {
      params: { appkey: appKey, appsecret: appSecret },
    });
    if (data.errcode !== 0) throw new Error(`gettoken failed: ${data.errmsg}`);
    tokenCache = { token: data.access_token, expires: now + (data.expires_in - 300) * 1000 };
    return data.access_token;
  }

  // OAuth2 v1.0 路径：钉钉 App 内 requestAuthCode 拿到 authCode，换企业内用户。
  async function getUserByAuthCode(authCode) {
    const token = await getAccessToken();

    const { data: infoRes } = await axios.post(
      `https://oapi.dingtalk.com/topapi/v2/user/getuserinfo?access_token=${token}`,
      { code: authCode },
    );
    if (infoRes.errcode !== 0) throw new Error(`getuserinfo failed: ${infoRes.errmsg}`);

    const userid = infoRes.result.userid;

    const { data: userRes } = await axios.post(
      `https://oapi.dingtalk.com/topapi/v2/user/get?access_token=${token}`,
      { userid },
    );
    if (userRes.errcode !== 0) throw new Error(`user/get failed: ${userRes.errmsg}`);

    const u = userRes.result;
    return {
      userId: u.userid,
      name: u.name,
      avatar: u.avatar,
      mobile: u.mobile || '',
      unionId: u.unionid,
    };
  }

  // 拼接钉钉扫码登录 URL（OAuth2 v1.0）。
  function getQrConnectUrl(redirectUri, state) {
    return `https://login.dingtalk.com/oauth2/auth?redirect_uri=${encodeURIComponent(redirectUri)}&client_id=${appKey}&response_type=code&scope=openid&state=${state}&prompt=consent`;
  }

  function normalizeError(err) {
    const msg = err.response?.data?.message || err.message || '';
    if (msg.includes('AccessTokenPermissionDenied')) return '无权限访问钉钉应用';
    if (msg.includes('invalid code')) return '授权码已过期';
    return msg || '钉钉接口错误';
  }

  // OAuth2 v1.0 路径：PC 扫码回调拿到 code，换用户信息（含 unionId 富化）。
  async function getUserByCode(code) {
    const { data: tokenRes } = await axios.post(
      'https://api.dingtalk.com/v1.0/oauth2/userAccessToken',
      { clientId: appKey, clientSecret: appSecret, code, grantType: 'authorization_code' },
    );
    if (tokenRes.message) throw new Error(normalizeError({ response: { data: tokenRes } }));

    const accessToken = tokenRes.accessToken;

    const { data: userRes } = await axios.get(
      'https://api.dingtalk.com/v1.0/contact/users/me',
      { headers: { 'x-acs-dingtalk-access-token': accessToken } },
    );

    const unionId = userRes.unionId || '';
    let realName = userRes.nickName || userRes.mobile || '未知用户';
    let mobile = userRes.mobile || '';

    if (unionId) {
      try {
        const corpToken = await getAccessToken();
        const { data: unionRes } = await axios.post(
          `https://oapi.dingtalk.com/topapi/user/getbyunionid?access_token=${corpToken}`,
          { unionid: unionId },
        );
        if (unionRes.errcode === 0 && unionRes.result?.userid) {
          const userid = unionRes.result.userid;
          const { data: detailRes } = await axios.post(
            `https://oapi.dingtalk.com/topapi/v2/user/get?access_token=${corpToken}`,
            { userid },
          );
          if (detailRes.errcode === 0) {
            realName = detailRes.result.name || realName;
            mobile = detailRes.result.mobile || mobile;
          }
        }
      } catch (err) {
        console.error('[dingtalk] getbyunionid error:', err.message);
      }
    }

    return {
      userId: userRes.openId || unionId,
      name: realName,
      avatar: userRes.avatarUrl || '',
      mobile: mobile,
      unionId: unionId,
    };
  }

  return { getAccessToken, getUserByAuthCode, getQrConnectUrl, getUserByCode };
}
