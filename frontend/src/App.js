<file>
<absolute_file_name>/app/frontend/src/App.js</absolute_file_name>
<content-replace><![CDATA[
          <Route path="/navigator/system-health" element={<NavigatorSystemHealth />} />
]]>:::<![CDATA[
          <Route path="/navigator/system-health" element={<NavigatorSystemHealth />} />
          <Route path="/login" element={<Login />} />
          {(process.env.REACT_APP_SHOW_RP_CRM || 'true').toLowerCase()==='true' && (
            <>
              <Route path="/rp" element={<RPLeadsList />} />
              <Route path="/rp/lead/:id" element={<RPLeadDetail />} />
              <Route path="/rp/requirements" element={<RPRequirementsAdmin />} />
              <Route path="/rp/share" element={<RPSharePage />} />
            </>
          )}
]]></content-replace>
</file>