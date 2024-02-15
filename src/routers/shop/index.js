// src/routers/shop/index.js

const express = require('express')
const {apiKey, permission} = require('../auth/checkAuth')
const router = express.Router()

router.use(apiKey)
router.use(permission('0000'))

router.use('/api/v1', require('./access'))

module.exports = router